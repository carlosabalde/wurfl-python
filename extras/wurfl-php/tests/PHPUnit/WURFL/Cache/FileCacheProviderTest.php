<?php
/**
 * test case
 */
require_once dirname(__FILE__).'/../classautoloader.php';

/**
 * test case.
 */
class WURFL_Cache_FileCacheProviderTest extends PHPUnit_Framework_TestCase {
	
	const CACHE_DIR = "../../../resources/cache";
		
	public function setUp() {
		WURFL_FileUtils::mkdir($this->cacheDir());
	}
	
	public function tearDown() {
		WURFL_FileUtils::rmdir($this->cacheDir());
	}
	
	
	public function testNeverToExpireItems() {
		$params = array(
			"dir" => $this->cacheDir(),
			WURFL_Configuration_Config::EXPIRATION => 0);
				
		$cache = new WURFL_Cache_FileCacheProvider($params);
		
		$cache->put("foo", "foo");
		sleep(1);
		$this->assertEquals("foo", $cache->get("foo"));
		
	}
	
	public function testShouldRemoveTheExpiredItem() {
		
		$params = array(
			"dir" => $this->cacheDir(),
			WURFL_Configuration_Config::EXPIRATION => 1);
				
		$cache = new WURFL_Cache_FileCacheProvider($params);
		
		$cache->put("item2", "item2");
		$this->assertEquals("item2", $cache->get("item2"));		
		sleep(2);
		$this->assertEquals(NULL, $cache->get("item2"));
	}
	
	private function cacheDir() {
		return 	dirname ( __FILE__ ) . DIRECTORY_SEPARATOR . self::CACHE_DIR;
		
	}
	
}
