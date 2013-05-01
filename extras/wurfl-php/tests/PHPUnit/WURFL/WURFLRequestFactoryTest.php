<?php
/**
 * test case
 */
require_once dirname(__FILE__).'/classautoloader.php';

class WURFLRequestFactoryTest extends PHPUnit_Framework_TestCase {
	
	const FILE_NAME = "../resources/request.yml";
	private $_genericRequestFactory;
	
	private $_testData = array ();
	
	public function setUp() {
		$userAgentNormalizer = new WURFL_Request_UserAgentNormalizer ( );
		$this->_genericRequestFactory = new WURFL_Request_GenericRequestFactory ( $userAgentNormalizer );
		$this->_testData = self::_loadData ( WURFLRequestFactoryTest::FILE_NAME );
	}
	
	public function testCreateRequest() {
		foreach ( $this->_testData as $testData ) {						
			$request = $this->_genericRequestFactory->createRequest ( $testData ["_SERVER"] );	
			if($request->userAgent != $testData["EXPECTED_USER_AGENT"]){ echo "Actual: [$request->userAgent], Expected: [{$testData["EXPECTED_USER_AGENT"]}]\n".var_export($testData['_SERVER'],true)."\n"; }	
			$this->assertEquals ( $request->userAgent, $testData ["EXPECTED_USER_AGENT"] );
		}
	
	}
	
	private static function _loadData($fileName) {
		$handle = fopen ( $fileName, "r" );
		$testData = array();
		$notNullCondition = new NotNullCondition();
		if ($handle) {
			while ( ! feof ( $handle ) ) {
				$line = fgets ( $handle, 4096 );
				if (strpos ( $line, "#" ) === false && strcmp ( $line, "\n" ) != 0) {
					$values = explode ( ":", trim ( $line ) );					
					$keys = array("HTTP_USER_AGENT","HTTP_X_DEVICE_USER_AGENT", "HTTP_X_SKYFIRE_VERSION","HTTP_X_BLUECOAT_VIA", "EXPECTED_USER_AGENT");					
					$serverData = self::arrayCombine($keys, $values, $notNullCondition);					
					$testData[] = array("_SERVER" => $serverData, "EXPECTED_USER_AGENT" => $serverData["EXPECTED_USER_AGENT"]);
					
				}
			}
			fclose ( $handle );
		}
		
		return $testData;
	}
	
	
	private static function arrayCombine(array $keys, array $values, NotNullCondition $condition=null) {
		if(is_null($condition)) {
			return array_combine($keys, $values);
		}
		$count = count($keys);
		$combinedArray = array();		
		for($i=0; $i<$count; $i++) {
			if($condition->check($keys[$i], $values[$i])) {
				$combinedArray[$keys[$i]] = $values[$i];				
			}
		}
		
		return $combinedArray;
	}

}

/**
 * Utility Classes
 *
 */
//interface Condition {
//	function check($key, $value);
//}

class NotNullCondition {
	public function check($key, $value) {
		return empty($key) || empty($value) ? FALSE : TRUE;	
	}
}

